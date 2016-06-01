-- Param
local function parsename(x)
  -- Expects parameter name in form name_1,2,3,
  local splitted = util.split(x,"_")
  assert(#splitted == 2)
  local id = splitted[1]
  local shape_str = util.split(splitted[2], ",")
  local shape = util.map(tonumber, shape_str)
  return id, shape
end

local function default_index(tbl, k)
  local id, shape = parsename(k)
  local new_val = t.rand(t.LongStorage(shape))
  tbl[k] = new_val
  return new_val
end

local function gen_param()
  local param = {}
  setmetatable(param,{
    __index = function(param,k) return default_index(param, k) end
  })
  return param
end


local function param_str(id, shape)
  return "%s_%s" % {id, util.tostring(shape)}
end