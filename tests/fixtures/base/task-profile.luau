--[[ @summary Exercise a host-only reviewed echo descriptor; this fixture is never installed. ]]
assert(type(base) == "table" and __simoder_base == nil)
local wire = '{"v":1,"schema":"test.echo@1","value":["u64","18446744073709551615"]}'
local value = assert(base.values.validate(wire, "test.echo@1"))
assert(base.values.wire(value) == wire)
local started, completed, failed, awaited, emitted = false, 0, 0, false, false
return {
    --[[ @summary Confirm initialization cannot bypass activation admission. ]]
    onEnable = function()
        local task, denial = base.request("fixture.echo", value)
        assert(task == nil and denial == "NotReady")
    end,
    --[[ @summary Exercise deferred callbacks, cancellation and native-registered await. ]]
    onTick = function()
        if not started then
            started = true
            local task = assert(base.request("fixture.echo", value))
            assert(task.poll().state == "queued")
            --[[ @summary Verify the exact successful task result. @param record Native copied outcome. ]]
            assert(task.onCompleted(function(record)
                assert(record.state == "succeeded" and record.committed)
                assert(base.values.wire(record.result) == wire)
                completed += 1
            end))
            --[[ @summary Await only inside the native-registered coroutine. ]]
            assert(base.run(function()
                local result = task.await()
                assert(result.state == "succeeded" and base.values.wire(result.result) == wire)
                awaited = true
            end))
            local cancelled = assert(base.request("fixture.echo", value))
            --[[ @summary Verify cancellation prevents the second native effect. @param record Terminal outcome. ]]
            assert(cancelled.onFailed(function(record)
                assert(record.state == "cancelled")
                failed += 1
            end))
            assert(cancelled.cancel() == "Ok")
        elseif not emitted and completed == 1 and failed == 1 and awaited then
            emitted = true
            print("BASE_TASK_PROFILE_COMPLETE")
        end
    end,
}
