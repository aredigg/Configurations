-- leader key (Space)
vim.g.mapleader = " "
-- line numbers
vim.opt.number = true
vim.opt.numberwidth = 6
vim.opt.signcolumn = 'yes:2'
-- editor
vim.opt.cursorline = true
vim.opt.expandtab = true
vim.opt.fillchars = { eob = "│" }
vim.opt.scrolloff = 2
vim.opt.shiftwidth = 4
vim.opt.wrap = false
vim.opt.guicursor = 'a:ver25-blinkwait700-blinkoff400-blinkon250'
-- i dont understand teh vimpaste
vim.keymap.set('n', 'p', 'P', { noremap = true })
vim.keymap.set('n', 'P', 'p', { noremap = true })
-- mouse
vim.opt.mousescroll = "ver:1,hor:1"
-- enable lsp
vim.lsp.enable('basedpyright')
vim.lsp.enable('sourcekit')
vim.lsp.enable('jdtls')
vim.lsp.enable('postgres_lsp')
vim.lsp.enable('rust-analyzer')
vim.lsp.enable('zls')
vim.lsp.enable('vhdl_ls')
vim.lsp.codelens.enable(true)
vim.lsp.inlay_hint.enable(true)

-- add inline error messages
vim.diagnostic.config({
  virtual_text = true,
  signs = true,
  underline = true,
  update_in_insert = true,
  float = { border = 'rounded', source = 'if_many' },
})

-- completion
vim.opt.completeopt = { 'menuone', 'nearest', 'noselect', 'popup' }
vim.opt.pumheight = 20
vim.api.nvim_create_autocmd('LspAttach', {
  callback = function(args)
    local client = vim.lsp.get_client_by_id(args.data.client_id)
    if client and client:supports_method('textDocument/completion') then
      vim.lsp.completion.enable(true, client.id, args.buf, {
        autotrigger = true,
      })
    end
  end,
})

-- code action
vim.keymap.set({ 'n' }, '<leader>ca', vim.lsp.buf.code_action, { desc = 'Perform code action' })

-- formatter
vim.api.nvim_create_autocmd('BufWritePre', {
  callback = function()
    vim.lsp.buf.format()
  end,
})

-- packages
vim.pack.add({
    'https://github.com/nvim-tree/nvim-web-devicons',
    'https://github.com/nvim-lualine/lualine.nvim',
    'https://github.com/nvim-tree/nvim-tree.lua',
})

-- lualine
local function progress_block()
  local cur = vim.fn.line('.')
  local tot = vim.fn.line('$')
  if tot > 0 then
    local pos = cur / tot
    if pos < 1/9 then
      return '█'
    elseif pos < 2/9 then
      return '▇'
    elseif pos < 3/9 then
      return '▆'
    elseif pos < 4/9 then
      return '▅'
    elseif pos < 5/9 then
      return '▄'
    elseif pos < 6/9 then
      return '▃'
    elseif pos < 7/9 then
      return '▂'
    elseif pos < 8/9 then
      return '▁'
    else
      return ' '
    end
  else
    return ' '
  end
end

local colors = {
    green = '#008000',
    blue = '#000080',
    black = '#000000',
    white = '#ffffff',
    catskill_white = '#eef7f7',
    golden_crust = '#ebac5b',
    burnt_sienna = '#e37256',
    cerise = '#d9386a',
    byzantine = '#b42bac',
    electric_purple = '#8f1ded',
    deep_indigo = '#31108a',
    midnight_blue = '#100144',
    fashion_blue = '#243bd3',
    trendy_darkblue = '#0c1eb2',
    pine_green = '#206d4b',
    neon_chartreuse = '#d9ff2f',
    stone = '#3e4b59',
    dim_gray = '#696969',
    solid_gray = '#969696',
    palette0 = '#232634',
    palette1 = '#d20f39',
    palette2 = '#40a02b',
    palette3 = '#727448',
    palette4 = '#1e66f5',
    palette5 = '#8839ef',
    palette6 = '#179299',
    palette7 = '#bcc0cc',
    palette8 = '#7c7f93',
    palette9 = '#e78284',
    palette10 = '#a6d189',
    palette11 = '#e5c890',
    palette12 = '#8caaee',
    palette13 = '#ca9ee6',
    palette14 = '#85c1dc',
    palette15 = '#dce0e8',
}

require("lualine").setup {
    options = {
	theme = {
              visual = {
                  a = { fg = colors.black, bg = colors.golden_crust, gui = 'bold' },
                  b = { fg = colors.burnt_sienna, bg = colors.black },
              },
              replace = {
                  a = { fg = colors.black, bg = colors.cerise, gui = 'bold' },
                  b = { fg = colors.byzantine, bg = colors.black },
              },
              inactive = {
                  c = { fg = colors.solid_gray, bg = colors.stone },
                  a = { fg = colors.catskill_white, bg = colors.dim_gray, gui = 'bold' },
                  b = { fg = colors.catskill_white, bg = colors.solid_gray },
              },
              normal = {
                  c = { fg = colors.catskill_white, bg = colors.midnight_blue },
                  a = { fg = colors.catskill_white, bg = colors.electric_purple, gui = 'bold' },
                  b = { fg = colors.catskill_white, bg = colors.deep_indigo },
              },
              insert = {
                  a = { fg = colors.catskill_white, bg = colors.fashion_blue, gui = 'bold' },
                  b = { fg = colors.catskill_white, bg = colors.trendy_darkblue },
              },
        },
	section_separators = { left = '', right = '' },
	component_separators = { left = '', right = '' }
    },
    sections = {
	lualine_a = {'mode'},
    	lualine_b = {'branch', 'diff', 'diagnostics'},
    	lualine_c = { {
		'filename',
	        symbols = {
		    modified = '',
		    readonly = '󱀰',
		    unnamed = '--',
		    newfile = '󰻭', 
	        }
	    }
    	},
    	lualine_x = {'encoding', {
		'fileformat',
		symbols = {
		    unix = '␊',
		    dos = '␍␊',
		    mac = '␍'
		}
	    }, 'filetype'},
    	lualine_y = { 'location' },
    	lualine_z = { progress_block }
    }
}

-- nvim-tree
vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1
require("nvim-tree").setup()
vim.keymap.set('n', '<leader>e', ':NvimTreeToggle<CR>', { desc = 'File explorer', silent = true })

