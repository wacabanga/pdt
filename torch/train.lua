local training = {}

-- Libs
-- local grad = require 'autograd'
-- local util = require 'autograd.util'
-- local lossFuns = require 'autograd.loss'
local optim = require 'optim'
local t = require 'torch'
local gen = require 'generators'
local dddt = require 'types'

function training.train(adt, num_epochs, save_every, sfx, save_dir)
  print("Starting Training")
  local loss_fn = dddt.get_loss_fn(adt.axioms, mse)
  local stats = {loss_vars = {}, loss_sums = {}}
  local params = adt:get_params()
  print(params)
  for epoch = 1, num_epochs do
    -- Initialise random variables
    for i = 1, #adt.randvars do
      adt.randvars[i].gen()
    end
    local loss = loss_fn(params)
    -- print(loss)
  end
end

return training