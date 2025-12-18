dap = require("dap")
dap.adapters.lldb = {
	type = 'executable',
	command = '/usr/local/bin/lldb-dap',
	name = 'lldb'
}
dap.configurations.c = {
	{
		name = 'Launch',
		type = 'lldb',
		request = 'launch',
		program = function()
			return vim.fn.input('Path to executable: ', vim.fn.getcwd() .. '/', 'file')
		end,
		cwd = '${workspaceFolder}',
		stopOnEntry = false,
		args = {}
	}
}
dap.configurations.cpp = dap.configurations.c
dap.configurations.rust = dap.configurations.c
dap.configurations.swift = dap.configurations.c
dap.adapters.python = function(cb, config)
	if config.request == 'attach' then
		---@diagnostic disable-next-line: undefined-field
		local port = (config.connect or config).port
		---@diagnostic disable-next-line: undefined-field
		local host = (config.connect or config).host or '127.0.0.1'
		cb({
			type = 'server',
			port = assert(port, '`connect.port` is required for a python `attach` configuration'),
			host = host,
			options = {
				source_filetype = 'python',
			},
		})
	else
		cb({
			type = 'executable',
			command = '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3',
			args = { '-m', 'debugpy.adapter' },
			options = {
				source_filetype = 'python',
			}
		})
	end
end
dap.configurations.python = {
	name = "Launch",
	type = 'python',
	request = 'launch',
	program = "${file}",
	pythonPath = function()
		return '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3'
	end
}
vim.keymap.set('n', '<space>db', function() require'dap'.toggle_breakpoint() end, {})
vim.keymap.set('n', '<space>dc', function() require'dap'.continue() end, {})
vim.keymap.set('n', '<space>di', function() require'dap'.step_into() end, {})
vim.keymap.set('n', '<space>do', function() require'dap'.step_over() end, {})
vim.keymap.set('n', '<space>dr', function() require'dap'.repl.open() end, {})

