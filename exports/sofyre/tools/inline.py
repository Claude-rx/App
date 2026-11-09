import re, base64, os, sys, mimetypes
d = sys.argv[1]; A = os.path.join(d, 'assets')
mt = {'woff2':'font/woff2','woff':'font/woff','ttf':'font/ttf','otf':'font/otf','svg':'image/svg+xml','webp':'image/webp','png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg','gif':'image/gif','css':'text/css','mp4':'video/mp4','ico':'image/x-icon','avif':'image/avif'}
def uri(name):
    ext = name.rsplit('.',1)[-1].lower()
    return f"data:{mt.get(ext,'application/octet-stream')};base64," + base64.b64encode(open(os.path.join(A,name),'rb').read()).decode()
def css_inline(css):
    css = re.sub(r'url\("([^"/]+\.(?!css)\w+)"\)', lambda m: f'url("{uri(m.group(1))}")' if os.path.exists(os.path.join(A,m.group(1))) else m.group(0), css)
    css = re.sub(r'@import "([^"]+\.css)"\s*;?', lambda m: css_inline(open(os.path.join(A,m.group(1))).read()), css)
    return css
html = open(os.path.join(d,'index.html')).read()
html = re.sub(r'<link\b[^>]*href="assets/([^"]+\.css)"[^>]*>', lambda m: '<style>' + css_inline(open(os.path.join(A,m.group(1))).read()) + '</style>', html)
html = re.sub(r'url\((["\']?)assets/([^"\')]+)\1\)', lambda m: f'url("{uri(m.group(2))}")', html)
html = re.sub(r'(["\'])assets/([^"\']+)\1', lambda m: f'{m.group(1)}{uri(m.group(2))}{m.group(1)}', html)
out = sys.argv[2]; open(out,'w').write(html)
print('left:', len(re.findall(r'["\(]assets/', html)), 'size MB:', round(os.path.getsize(out)/1e6,1))
