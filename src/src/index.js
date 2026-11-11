import { registerRoute } from "@/plugins";
import ExecOnMcode from "./ExecOnMcode.vue";

registerRoute(ExecOnMcode, {
    Preferences: { ExecOnMcode: {
        icon: "mdi-powershell", caption: "ExecOnMcode", translated: true,
        path: "/ExecOnMcode"
    } }
});
