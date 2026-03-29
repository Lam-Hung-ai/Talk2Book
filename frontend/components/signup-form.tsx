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
import { signInWithGoogle } from "@/lib/auth-client"
import * as z from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { toast } from "sonner"
import { useRouter } from "next/navigation"
import { signUp } from "@/server/user"
import { Controller, useForm } from "react-hook-form"
import Link from "next/link"
import { GoogleIcon } from "@/components/icons/google"
import { useState } from "react";
import { Loader2Icon } from "lucide-react";


const formSchema = z.object({
  name: z.string().min(1, { message: "Họ và tên không được để trống" }).max(50, { message: "Họ và tên không được vượt quá 50 ký tự" }),
  email: z.email({ message: "Định dạng email không hợp lệ" }),
  password: z.string().min(8, { message: "Mật khẩu phải có ít nhất 8 ký tự" }),
  confirmPassword: z.string().min(8, { message: "Mật khẩu phải có ít nhất 8 ký tự" }),
})

export function SignupForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  })

  async function onSubmit(data: z.infer<typeof formSchema>) {
    setIsLoading(true)
    if (data.password !== data.confirmPassword) {
      toast.error("Mật khẩu và xác nhận mật khẩu không khớp. Vui lòng thử lại.")
      return
    }
    try {
      await signUp(data.name, data.email, data.password)
    } catch (error) {
      toast.error("Email đã tồn tại. Vui lòng thay đổi email hoặc đăng nhập với email đó.")
      setIsLoading(false)
      return
    }
    toast.success("Đăng ký thành công")
    setIsLoading(false)
    router.push("/")
  }
  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="overflow-hidden p-0">
        <CardContent className="grid p-0 md:grid-cols-2">
          <form className="p-6 md:p-8" id="signup-form" onSubmit={form.handleSubmit(onSubmit)}>
            <FieldGroup>
              <div className="flex flex-col items-center gap-2 text-center">
                <h1 className="text-2xl font-bold">Tạo tài khoản</h1>
                <p className="text-sm text-balance text-muted-foreground">
                    Nhập thông tin dưới đây để tạo tài khoản
                </p>
              </div>
              <Controller 
                name="name"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="signup-form-name">Họ và tên</FieldLabel>
                    <Input id="signup-form-name" type="text" {...field} aria-invalid={fieldState.invalid} required placeholder="Nguyễn Văn A" />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
              <Controller  
                name="email"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="signup-form-email">Email</FieldLabel>
                    <Input id="signup-form-email" type="email" {...field} aria-invalid={fieldState.invalid} required  placeholder="m@example.com" />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
              <Field className="grid grid-cols-2 gap-4">
                <Controller 
                  name="password"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="signup-form-password">Mật khẩu</FieldLabel>
                      <Input id="signup-form-password" type="password" {...field} aria-invalid={fieldState.invalid} required placeholder="******" />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />

                <Controller 
                  name="confirmPassword"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="signup-form-confirm-password">Xác nhận mật khẩu</FieldLabel>
                      <Input id="signup-form-confirm-password" type="password" {...field} aria-invalid={fieldState.invalid} required placeholder="******" />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
              </Field>
              <FieldDescription>
                Mật khẩu phải có ít nhất 8 ký tự.
              </FieldDescription>
              <Field>
                <Button type="submit" id="signup-form" disabled={isLoading}>
                  {isLoading ? <Loader2Icon className="size-4 animate-spin" /> : "Tạo mới"}
                </Button>
              </Field>
              <FieldSeparator className="*:data-[slot=field-separator-content]:bg-card">
                Hoặc tiếp tục với
              </FieldSeparator>
              <Field>
                <Button variant="outline" type="button" onClick={signInWithGoogle}>
                  <GoogleIcon />
                  <span>Đăng ký với Google</span>
                </Button>
              </Field>
              <FieldDescription className="text-center">
                Bạn đã có tài khoản? <Link href="/login">Đăng nhập</Link>
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
