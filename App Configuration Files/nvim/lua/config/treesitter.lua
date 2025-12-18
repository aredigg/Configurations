-- import nvim-treesitter plugin safely
local status, treesitter = pcall(require, "nvim-treesitter.configs")
if not status then
    return
end

-- configure treesitter
treesitter.setup({
    -- enable syntax highlighting
    highlight = {
        enable = true,
    },
    -- enable indentation
    indent = { enable = true },
    -- ensure these language parsers are installed
    ensure_installed = {
        "arduino",
        "c",
        "cmake",
        "cpp",
        "css",
        "dockerfile",
        "go",
        "html",
        "java",
        "javascript",
        "json",
        "kotlin",
        -- "latex",
        "lua",
        "make",
        "markdown",
        "markdown_inline",
        "nginx",
        "powershell",
        "python",
        "r",
        "rust",
        "sql",
        -- "swift",
        "toml",
        "typescript",
        "vhdl",
        "vim",
        "xml",
        "yaml",
        "zig"
    },
    -- auto install above language parsers
    auto_install = true,
})
