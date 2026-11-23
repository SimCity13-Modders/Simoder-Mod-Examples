--!strict
--[[ @summary Demonstrates a source mod with isolated lifecycle callbacks and a local module. ]]
local greeting = require("./greeting")
local elapsed = 0

return {
    --[[ @summary Runs in the candidate sandbox; messages publish only after activation succeeds. ]]
    onEnable = function()
        simoder.log(greeting.message .. " " .. simoder.modId)
    end,
    --[[ @summary Receives background wall time, independent of the game's simulation and render frame. ]]
    onTick = function(deltaSeconds: number)
        elapsed += deltaSeconds
        if elapsed >= 5 then
            elapsed = 0
            simoder.log("Luau is running")
        end
    end,
    --[[ @summary Runs once when disabled or replaced by a new script generation. ]]
    onDisable = function()
        simoder.log("Luau example stopped")
    end,
}
