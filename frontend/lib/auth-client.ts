import { createAuthClient } from "better-auth/react"
export const authClient = createAuthClient({
    /** The base URL of the server (optional if you're using the same domain) */
    baseURL: process.env.BETTER_AUTH_URL!,
})

export const signInWithGoogle = async () => {
    await authClient.signIn.social({
    provider: "google",
    callbackURL: process.env.BETTER_AUTH_URL!,
    });
}
