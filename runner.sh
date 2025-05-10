brew install nasm
nasm -f "macho64" "hello".asm 
ld -e "_code" -static "filename".o -o "filename".out 
./filename.out