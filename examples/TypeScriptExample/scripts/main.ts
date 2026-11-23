import { greeting } from "./greeting";

/** @summary Emits a mod-attributed message when the compiled generation is activated. */
export function onEnable(): void {
    simoder.log(`${greeting} ${simoder.modId}`);
}

/** @summary Emits one lifecycle message when the generation is disabled. */
export function onDisable(): void {
    simoder.log("TypeScript example stopped");
}
