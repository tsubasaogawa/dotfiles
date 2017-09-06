set number
set autoindent
set expandtab
set list
set listchars=tab:>\ ,trail:-
set showmatch
set autoread
set incsearch
set cursorline
set backspace=indent,eol,start
set nocompatible
set tabstop=4
set shiftwidth=2
set cindent
set showcmd
set laststatus=2
set fenc=utf-8
set virtualedit=onemore
set wildmode=list:longest
set ignorecase
set smartcase
set wrapscan
set display=lastline
set hidden

nmap <Esc><Esc> :nohlsearch<CR><Esc>

" :W sudo saves the file
" (useful for handling the permission-denied error)
command W w !sudo tee % > /dev/null

" Note: Skip initialization for vim-tiny or vim-small.
 if 0 | endif

 if &compatible
   set nocompatible               " Be iMproved
 endif

 " Required:
 set runtimepath+=~/.vim/bundle/neobundle.vim/

 " Required:
 call neobundle#begin(expand('~/.vim/bundle/'))

 " Let NeoBundle manage NeoBundle
 " Required:
 NeoBundleFetch 'Shougo/neobundle.vim'

 " My Bundles here:
 " Refer to |:NeoBundle-examples|.
 " Note: You don't set neobundle setting in .gvimrc!

  NeoBundle 'itchyny/lightline.vim'

  " ColorScheme
  NeoBundle 'jeetsukumaran/vim-nefertiti'
  NeoBundle 'jacoborus/tender.vim'
  NeoBundle 'gosukiwi/vim-atom-dark'
  NeoBundle 'aereal/vim-colors-japanesque'
  NeoBundle 'romainl/Apprentice'
  NeoBundle 'raphamorim/lucario'
 call neobundle#end()

 " Required:
 filetype plugin indent on

 " If there are uninstalled bundles found on startup,
 " this will conveniently prompt you to install them.
 NeoBundleCheck

syntax enable
set t_Co=256
colorscheme apprentice
let g:lightline = { 'colorscheme': 'tender' }
