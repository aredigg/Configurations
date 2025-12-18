local lint = require("lint")
lint.linters_by_ft = {
	swift = { "swiftlint" },
	c = { "clangtidy" },
	cpp = { "clangtidy" },
	python = { "pylint" }
}
local lint_augroup = vim.api.nvim_create_augroup("lint", { clear = true })
vim.api.nvim_create_autocmd({ "BufWritePost", "BufReadPost", "InsertLeave", "TextChanged" }, {
	group = lint_augroup,
	callback = function()
		require("lint").try_lint()
	end
})
vim.keymap.set("n", "<leader>ml", function()
	lint.try_lint()
end, { desc = "Lint file" })
vim.keymap.set('n', '<leader>ca', function()
    vim.lsp.buf.code_action({apply=true}) end, {})
vim.keymap.set('t', '<esc>', [[<C-\><C-n>]], {})
