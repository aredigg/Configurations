local conform = require("conform")
conform.setup {
	formatters_by_ft = {
		swift = { "swiftformat" },
		c = { "clang-format" },
		cpp = { "clang-format" },
		python = { "isort", "black" }
	},
	format_on_save = function(bufnr)
		return { timeout_ms = 500, lsp_fallback = true }
	end,
	log_level = vim.log.levels.ERROR
}
vim.keymap.set({ "n", "v" }, "<leader>mp", function()
	conform.format({
		lsp_fallback = true,
		async = false,
		timeout_ms = 500
	})
end, { desc = "Format file or range (in visual mode)" })
