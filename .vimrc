set ic
set number
set nocompatible
set ignorecase
set relativenumber
"set cursorcolumn
set cursorline
"set listchars=tab:\|\
"set list
"set nowrap
syntax on
set nocompatible              " be iMproved, required
filetype on                  " required

"set splitbelow
"set splitright
"split navigations
nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>
nnoremap <C-H> <C-W><C-H>

" Enable folding
set foldmethod=indent
set foldlevel=99

" Enable folding with the spacebar
nnoremap <space> za
let g:SimpylFold_docstring_preview=1

" PEP 8 indentation
au BufNewFile,BufRead *.py
\ set tabstop=4 |
\ set softtabstop=4 |
\ set shiftwidth=4 |
"\ set textwidth=79 |
\ set expandtab |
\ set autoindent |
\ set fileformat=unix

"remember there is not space between file type
"autocmd FileType js,html,css
"au BufNewFile,BufRead *.js,*.json,*.html,*.css
au BufNewFile,BufRead *.c,*.js,*.json,*.html
\ set expandtab |
\ set tabstop=2 |
\ set softtabstop=2 |
\ set shiftwidth=2

"au BufRead,BufNewFile *.py,*.pyw,*.c,*.h match BadWhitespace /\s\+$/

set encoding=utf-8
set guifont=Bitstream\ Vera\ Sans\ Mono:h14

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'
Plugin 'gisphm/vim-gitignore'
Plugin 'mattn/emmet-vim'

"Plugin 'Valloric/YouCompleteMe'
"let g:ycm_autoclose_preview_window_after_completion=1
"map <leader>g  :YcmCompleter GoToDefinitionElseDeclaration<CR>

" trigger after type 2 charactor
" first load by ctrl+space
"let g:ycm_semantic_triggers = {'python': [ 're!\w{2}' ]}
"let g:ycm_semantic_triggers = {
"	\ 'python': [ 're!(import\s+|from\s+(\w+\s+(import\s+(\w+,\s+)*)?)?)' ],
"	\ 'c': ['->', '.']
"	\ }

" white language when ctrl-space
"let g:ycm_filetype_whitelist = {"c":1,"cpp":1,"python":1}


" The following are examples of different formats supported.
" Keep Plugin commands between vundle#begin/end.
" plugin on GitHub repo
"Plugin 'tpope/vim-fugitive'
" plugin from http://vim-scripts.org/vim/scripts.html
" Plugin 'L9'
" Git plugin not hosted on GitHub
"Plugin 'git://git.wincent.com/command-t.git'
" git repos on your local machine (i.e. when working on your own plugin)
"Plugin 'file:///home/gmarik/path/to/plugin'
" The sparkup vim script is in a subdirectory of this repo called vim.
" Pass the path to set the runtimepath properly.
"Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}
" Install L9 and avoid a Naming conflict if you've already installed a
" different version somewhere else.
" Plugin 'ascenator/L9', {'name': 'newL9'}

" All of your Plugins must be added before the following line
"
"
"
"Plugin 'arzg/vim-colors-xcode'
"Plug 'morhetz/gruvbox'
"Plug 'ervandew/supertab'
Plugin 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }
" FZF key map
nnoremap <C-f> :FZF<CR>
"nnoremap ; : FZF<CR>
"nnoremap <S-F4> : FZF<CR>

"Plug 'junegunn/fzf.vim'
Plugin 'itchyny/lightline.vim'
Plugin 'mengelbrecht/lightline-bufferline'
"Plugin 'ParamagicDev/vim-medic_chalk'
"colorscheme medic_chalk
"
"Plugin 'NLKNguyen/papercolor-theme'
Plugin 'morhetz/gruvbox'


call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line
"
"
"
" status bar line
set laststatus=2
" lighline-bufferline
set showtabline=2
" fix MacVim
set guioptions-=e

let g:lightline#bufferline#show_number=1
let g:lightline#bufferline#shorten_path=0
let g:lightline#bufferline#unnamed='[No Name]'

let g:lightline={}
let g:lightline.tabline={'left': [['buffers']], 'right': [['close']]}
let g:lightline.component_expand={'buffers': 'lightline#bufferline#buffers'}
let g:lightline.component_type={'buffers': 'tabsel'}
" disable path show only filename
"let g:lightline#bufferline#filename_modifier=':t'

let g:python_highlight_all=1
"let g:PaperColor_Theme_Options = {
"  \   'language': {
"  \     'python': {
"  \       'highlight_builtins' : 1
"  \     },
"  \     'cpp': {
"  \       'highlight_standard_library': 1
"  \     },
"  \     'c': {
"  \       'highlight_builtins' : 1
"  \     }
"  \   }
"  \ }
"set background=dark
"colorscheme PaperColor

"let g:user_emmet_mode='a'
let g:user_emmet_install_global=0
autocmd FileType html,css EmmetInstall


colorscheme darkblue
