--[[ @summary Demonstrates a named owner-scoped override; the loader restores other owners or vanilla on disable. ]]
return {
    onEnable = function()
        if not simoder.hasCapability("game.props.float") then
            simoder.log("PROP API requires the attached loader host")
            return
        end
        local observed = simoder.props.getFloat("sanitizer", "operatingCost")
        if observed then
            simoder.log("Last observed cost: " .. tostring(observed.value))
        end
        simoder.props.setFloat("sanitizer", "operatingCost", 345)
    end,
    onDisable = function()
        simoder.log("PROP example stopped; loader removes its owned override")
    end,
}
