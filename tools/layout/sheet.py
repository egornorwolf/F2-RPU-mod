import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from render import frm
from PIL import Image, ImageDraw
def sheet(paths, out, cols=6):
    ims=[(p.split('\\')[-1], frm(p)) for p in paths]
    ims=[(l,r[0]) for l,r in ims if r]
    cw=max(i.width for _,i in ims)+10; ch=max(i.height for _,i in ims)+24
    rows=(len(ims)+cols-1)//cols
    sh=Image.new('RGB',(cw*cols,ch*rows),(60,50,40)); dr=ImageDraw.Draw(sh)
    for k,(l,im) in enumerate(ims):
        x=(k%cols)*cw; y=(k//cols)*ch
        sh.paste(im,(x+5,y+5),im); dr.text((x+5,y+ch-16),l,fill=(255,255,200))
    sh.save(out)
if __name__=='__main__': sheet(sys.argv[2:], sys.argv[1])
