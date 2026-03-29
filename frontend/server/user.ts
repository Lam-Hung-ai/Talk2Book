"use server";
import { auth } from "@/lib/auth";

export const signIn = async (email: string, password: string) => {
    await auth.api.signInEmail({
        body: {
            email: email,
            password: password,
            rememberMe: true,
        }
    })
}

export const signUp = async (name: string, email: string, password: string) => {
    await auth.api.signUpEmail({
        body: {
        email: email,
        password: password,
        name: name,
        },
  });
};