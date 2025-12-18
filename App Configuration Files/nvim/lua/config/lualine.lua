local function progress_2()
  local cur = vim.fn.line('.')
  local total = vim.fn.line('$')
  if cur == 1 then
    return '⤒'
  elseif cur == total then
    return '⤓'
  else
    return ' '
  end
end

local function progress_3()
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

require("lualine").setup {
    options = {
	theme = 'ayu_dark',
	section_separators = { left = '', right = '' },
	component_separators = { left = '', right = '' }
    },
    sections = {
	lualine_a = {'mode'},
    	lualine_b = {'branch', 'diff', 'diagnostics'},
    	lualine_c = {
	    {
		'filename',
	        symbols = {
		    modified = '',
		    readonly = '󱀰',
		    unnamed = '--',
		    newfile = '󰻭', 
	        }
	    }
    	},
    	lualine_x = {'encoding',
	    {
		'fileformat',
		symbols = {
		    unix = '␊',
		    dos = '␍␊',
		    mac = '␍'
		}
	    }, 'filetype'},
    	lualine_y = { 'location' },
    	lualine_z = { progress_3 }
    }
}
