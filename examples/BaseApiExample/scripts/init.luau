--[[ @summary Observe the supported Base profile without requesting effects or permissions. ]]
local available, subscribed, observed, completed = false, false, false, false
return {
    --[[ @summary Handle an unbound runtime without assuming Base is available. ]]
    onEnable = function()
        if type(base) ~= "table" then
            print("BASE_API_EXAMPLE_UNAVAILABLE")
            return
        end
        assert(table.isfrozen(base))
        available = true
    end,
    --[[ @summary Subscribe after admission and verify deferred, copied lifecycle state. ]]
    onTick = function()
        if not available or completed then return end
        if not subscribed then
            local snapshot, denial = base.snapshot()
            if snapshot == nil then
                print("Base snapshot unavailable: " .. tostring(denial))
                return
            end
            assert(table.isfrozen(snapshot))
            assert(type(snapshot.sequence) == "string" and type(snapshot.baseEpoch) == "string")
            --[[ @summary Independent reads can observe a concurrent publication; no equality is promised. ]]
            local repeated, repeatedDenial = base.snapshot()
            if repeated == nil then
                print("Base snapshot unavailable: " .. tostring(repeatedDenial))
                return
            end
            assert(table.isfrozen(repeated) and type(repeated.sequence) == "string")
            --[[ @summary Observe one copied lifecycle record. @param record Snapshot or nil. @param reason Denial if unavailable. ]]
            local registration, failure = base.subscribe(function(record, reason)
                if record == nil then
                    print("Base subscription unavailable: " .. tostring(reason))
                    return
                end
                assert(table.isfrozen(record) and type(record.sequence) == "string")
                observed = true
            end)
            if registration == nil then
                print("Base subscription denied: " .. tostring(failure))
                return
            end
            assert(not observed)
            subscribed = true
        elseif observed then
            local catalog, denial = base.descriptors()
            if catalog == nil then
                print("Base catalog unavailable: " .. tostring(denial))
                return
            end
            assert(table.isfrozen(catalog))
            completed = true
            print("BASE_API_EXAMPLE_COMPLETE")
        end
    end,
}
