#!/usr/bin/env bash
# Build the two tools that change what a person says in a video, on a CPU-only machine (no GPU needed):
#   <dir>/cb    Chatterbox (Resemble AI, MIT) for tools/persona/voice_edit.py: new words in the speaker's own voice
#   <dir>/ls    LatentSync 1.5 (ByteDance, Apache-2.0 code, OpenRAIL++ weights): the mouth says the new words
#               (code in <dir>/LatentSync)
# Both licences allow commercial use. Not F5-TTS, VoiceCraft, MaskGCT or XTTS: their weights are non-commercial.
#
# usage: tools/persona/setup_voice_tools.sh <dir>      (about 7 GB: PyTorch, Chatterbox 3.2 GB, LatentSync 2.5 GB)
# Then:
#   <dir>/cb/bin/python tools/persona/voice_edit.py ...                       (see its docstring)
#   cd <dir>/LatentSync && ../ls/bin/python -m scripts.inference --unet_config_path configs/unet/stage2.yaml \
#     --inference_ckpt_path checkpoints/latentsync_unet.pt --inference_steps 20 --guidance_scale 1.5 \
#     --video_path clip.mp4 --audio_path clip.wav --video_out_path synced.mp4 --temp_dir tmp
#     (on 4 CPU cores: about 38 s a step for each 16 frames at 25 fps, so a 1.28 s clip takes 25 minutes)
#   tools/persona/mouth_patch.py puts the synced mouth back on the source video's own frames (see its docstring)
set -euo pipefail
D=$(mkdir -p "$1" && cd "$1" && pwd)
CPU=(--extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match)

uv venv -q --python python3.11 "$D/cb"
VIRTUAL_ENV="$D/cb" uv pip install -q torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
# setuptools < 81 keeps pkg_resources, which Chatterbox's audio watermark (perth) still imports
VIRTUAL_ENV="$D/cb" uv pip install -q chatterbox-tts faster-whisper praat-parselmouth "setuptools<81" "${CPU[@]}"

[ -d "$D/LatentSync" ] || git clone -q https://github.com/bytedance/LatentSync "$D/LatentSync"
cd "$D/LatentSync"
uv venv -q --python python3.11 "$D/ls"
VIRTUAL_ENV="$D/ls" uv pip install -q torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu
# its requirements, with the CPU build of onnxruntime and without the GPU-only and web-UI packages
grep -vE '^torch|extra-index|onnxruntime-gpu|gradio|mediapipe' requirements.txt > "$D/ls-req.txt"
echo 'onnxruntime==1.21.0' >> "$D/ls-req.txt"
VIRTUAL_ENV="$D/ls" uv pip install -q -r "$D/ls-req.txt"

# LatentSync assumes a GPU; these five edits run it on the CPU (insightface face detection included)
sed -i 's/^\(    def __init__(self, align_points=3, resolution=256, device="cpu", dtype=torch.float16):\)$/\1\n        if str(device) == "cpu": dtype = torch.float32  # the CPU cannot warp half-precision images/' latentsync/utils/affine_transform.py
sed -i 's/providers=\["CUDAExecutionProvider"\],/providers=["CPUExecutionProvider"] if device == "cpu" else ["CUDAExecutionProvider"],/; s/self.app.prepare(ctx_id=cuda_to_int(device),/self.app.prepare(ctx_id=-1 if device == "cpu" else cuda_to_int(device),/' latentsync/utils/face_detector.py
sed -i 's/ImageProcessor(height, device="cuda", mask_image=mask_image)/ImageProcessor(height, device=str(device), mask_image=mask_image)/' latentsync/pipelines/lipsync_pipeline.py
sed -i 's/        device="cuda",/        device="cpu",/; s/    ).to("cuda")/    ).to("cpu")/' scripts/inference.py
"$D/ls/bin/python" - <<'EOF'
p = 'latentsync/utils/image_processor.py'; s = open(p).read()
a = '''        if device == "cpu":
            self.face_detector = None
        else:
            self.face_detector = FaceDetector(device=device)'''
if a in s: open(p, 'w').write(s.replace(a, '        self.face_detector = FaceDetector(device=device)  # insightface runs on the CPU too'))
EOF

# weights: LatentSync 1.5 (256 px faces), its Whisper encoder, the insightface detector (a Hugging Face copy of
# buffalo_l: its GitHub release is often unreachable from sandboxes) and the SD VAE. The 5 GB float32 UNet is kept
# as float16 (2.5 GB); it is cast back to float32 when it loads on the CPU.
"$D/ls/bin/python" - <<'EOF'
import os, torch
from huggingface_hub import hf_hub_download
from diffusers import AutoencoderKL
for f in ['whisper/tiny.pt', 'latentsync_unet.pt']: hf_hub_download('ByteDance/LatentSync-1.5', f, local_dir='checkpoints')
for f in ['det_10g.onnx', '2d106det.onnx']:
    hf_hub_download('vjump21848/buffalo_l_unzip', f, local_dir='checkpoints/auxiliary/models/buffalo_l')
AutoencoderKL.from_pretrained('stabilityai/sd-vae-ft-mse')
p = 'checkpoints/latentsync_unet.pt'
ck = torch.load(p, map_location='cpu', weights_only=False)
if any(v.dtype == torch.float32 for v in ck['state_dict'].values() if torch.is_tensor(v)):
    ck['state_dict'] = {k: v.half() if torch.is_tensor(v) and v.dtype == torch.float32 else v for k, v in ck['state_dict'].items()}
    torch.save(ck, p + '.fp16'); os.replace(p + '.fp16', p)
EOF
echo "voice tools ready in $D"
