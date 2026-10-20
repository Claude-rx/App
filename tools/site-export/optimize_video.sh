#!/usr/bin/env bash
# Re-encode export videos to web size in place: max 720px on the short side, H.264 CRF 26, AAC 96k, faststart.
# Keeps the file name; only replaces a file when the result is smaller.  usage: optimize_video.sh <export_dir>
set -u
shopt -s nullglob
enc() {
  f="$1"; t="${f%.mp4}.opt.mp4"
  ffmpeg -nostdin -loglevel error -y -i "$f" \
    -vf "scale='if(gt(iw,ih),-2,min(720,iw))':'if(gt(iw,ih),min(720,ih),-2)'" \
    -c:v libx264 -preset veryfast -crf 26 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart "$t" \
  && [ "$(stat -c%s "$t")" -lt "$(stat -c%s "$f")" ] && mv "$t" "$f" || rm -f "$t"
}
export -f enc
ls "$1"/assets/media/*.mp4 | xargs -P "$(nproc)" -I{} bash -c 'enc "$@"' _ {}
du -sh "$1"/assets/media
