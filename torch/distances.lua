local t = torch
distances = {}
function distances.mse(a, b)
  print("a", a)
  print("b", b)
  local a_b = a - b
  return t.sum(t.cmul(a_b, a_b))
end

return distances