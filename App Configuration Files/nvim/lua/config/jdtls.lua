local jdtls = require("jdtls")
local config = {
    cmd = { '/usr/local/bin/jdtls' },
    root_dir = vim.fs.dirname(vim.fs.find({ 'gradlew', '.git', 'mvnw' }, { upward = true })[1])
}
vim.api.nvim_create_autocmd("FileType", {
    pattern = "java",
    callback = function()
        jdtls.start_or_attach(config)
    end,
})
