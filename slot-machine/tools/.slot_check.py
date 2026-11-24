import re,sys
src=open(sys.argv[1],encoding='utf-8').read()
m=re.search(r'<script>(.*)</script>',src,re.S)
s=m.group(1)
mode=['code'];stack=[];errors=[];line=1;i=0;n=len(s)
while i<n:
    ch=s[i];nx=s[i+1] if i+1<n else ''
    if ch=='\n':line+=1
    cur=mode[-1]
    if cur=='line':
        if ch=='\n':mode.pop()
        i+=1;continue
    if cur=='block':
        if ch=='*' and nx=='/':mode.pop();i+=2;continue
        i+=1;continue
    if cur=='str':
        if ch=='\\':i+=2;continue
        if ch==stack[-1][0]:stack.pop();mode.pop()
        i+=1;continue
    if cur=='tpl':
        if ch=='\\':i+=2;continue
        if ch=='$' and nx=='{':stack.append(('${',line));mode.append('code');i+=2;continue
        if ch=='`':stack.pop();mode.pop();i+=1;continue
        i+=1;continue
    # code
    if ch=='/' and nx=='/':mode.append('line');i+=2;continue
    if ch=='/' and nx=='*':mode.append('block');i+=2;continue
    if ch in '"\'':stack.append((ch,line));mode.append('str');i+=1;continue
    if ch=='`':stack.append(('`',line));mode.append('tpl');i+=1;continue
    if ch in '([{':stack.append((ch,line));i+=1;continue
    if ch in ')]}':
        if not stack:errors.append('extra %s line %d'%(ch,line));i+=1;continue
        o,ol=stack.pop()
        if o=='${' and ch=='}':
            mode.pop();i+=1;continue
        pair={'(':')','[':']','{':'}'}
        if pair.get(o)!=ch:errors.append('mismatch %s(line %d) vs %s(line %d)'%(o,ol,ch,line))
        i+=1;continue
    i+=1
print('unclosed:',len(stack),stack[:5])
print('errors:',len(errors),errors[:5])