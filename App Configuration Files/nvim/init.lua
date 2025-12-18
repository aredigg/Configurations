-- leader key
vim.g.mapleader = 'C-<space>'
-- colors
vim.opt.termguicolors = true
-- plugin configurations
require("config.lazy")
require("config.lualine")
require("config.lspconfig")
require("config.lint")
require("config.conform")
require("config.dap")
require("config.dap-ui")
require("config.jdtls")
require("config.treesitter")
-- line numbers
vim.opt.nu = true
vim.opt.nuw = 6
-- editor
vim.opt.cul = true
vim.opt.et = true
vim.opt.fcs = { eob = "│" }
vim.opt.so = 2
vim.opt.sw = 4
-- mouse
vim.opt.mousescroll = "ver:1,hor:1"
