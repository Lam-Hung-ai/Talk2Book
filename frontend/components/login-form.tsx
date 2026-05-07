"use client";
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldSeparator,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { signIn } from "@/server/user"
import * as z from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { toast } from "sonner"
import { Controller, useForm } from "react-hook-form"
import { useRouter } from "next/navigation";
import Link from "next/link";
import { GoogleIcon } from "@/components/icons/google"
import { useState } from "react";
import { Loader2Icon } from "lucide-react";
import { signInWithGoogle } from "@/lib/auth-client";

const formSchema = z.object({
  email: z.email({ message: "Định dạng email không hợp lệ" }),
  password: z.string().min(8, { message: "Mật khẩu phải có ít nhất 8 ký tự" }),
})

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  })

  async function onSubmit(data: z.infer<typeof formSchema>) {
    setIsLoading(true)
    try {
      await signIn(data.email, data.password)
    } catch (error) {
      toast.error("Email hoặc mật khẩu không chính xác")
      console.error(error)
      setIsLoading(false)
      return
    }
    toast.success("Đăng nhập thành công")
    setIsLoading(false)
    router.push("/")
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="overflow-hidden p-0">
        <CardContent className="grid p-0 md:grid-cols-2">
          <form className="p-6 md:p-8" id="login-form" onSubmit={form.handleSubmit(onSubmit)}>
            <FieldGroup>
              <div className="flex flex-col items-center gap-2 text-center">
                <h1 className="text-2xl font-bold">Chào mừng bạn trở lại</h1>
                <p className="text-balance text-muted-foreground">
                  Hãy bắt đầu khám phá những chuyến đi mới
                </p>
              </div>
              <Controller
                name="email"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="login-form-email">Email</FieldLabel>
                    <Input
                      id="login-form-email"
                      type="email"
                      placeholder="m@example.com"
                      {...field}
                      aria-invalid={fieldState.invalid}
                      required
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
              <Controller
                name="password"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <div className="flex items-center">
                      <FieldLabel htmlFor="login-form-password">Mật khẩu</FieldLabel>
                      <Link href="/forgot-password" className="ml-auto text-sm underline-offset-2 hover:underline">Quên mật khẩu? </Link>
                    </div>
                    <Input
                      id="login-form-password"
                      type="password"
                      placeholder="********"
                      {...field}
                      aria-invalid={fieldState.invalid}
                      required
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
              <Field>
                <Button type="submit" id="login-form" disabled={isLoading}>
                  {isLoading ? <Loader2Icon className="size-4 animate-spin" /> : "Đăng nhập"}
                </Button>
              </Field>
              <FieldSeparator className="*:data-[slot=field-separator-content]:bg-card">
                Hoặc tiếp tục với
              </FieldSeparator>
              <Field>
                <Button variant="outline" type="button" onClick={signInWithGoogle}>
                  <GoogleIcon />
                  <span>Đăng nhập với Google</span>
                </Button>
              </Field>
              <FieldDescription className="text-center">
                Bạn chưa có tài khoản? <Link href="/signup">Đăng ký</Link>
              </FieldDescription>
            </FieldGroup>
          </form>
          <div className="relative hidden md:block">
            <img
              src="/logo_remove_background.png"
              alt="Talk2Book Logo"
              className="absolute inset-0 h-full w-full object-contain"
            />
          </div>
        </CardContent>
      </Card>
      <FieldDescription className="px-6 text-center">
        Bằng cách tiếp tục, bạn đồng ý với <a href="#">Điều khoản dịch vụ</a>{" "}
        và <a href="#">Chính sách bảo mật</a>.
      </FieldDescription>
    </div>
  )
}
