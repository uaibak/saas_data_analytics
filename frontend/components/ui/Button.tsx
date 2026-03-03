import clsx from "clsx";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  isLoading?: boolean;
};

export default function Button({ children, className, disabled, isLoading, ...props }: ButtonProps) {
  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      className={clsx(
        "inline-flex h-10 items-center justify-center rounded-md bg-brand-600 px-4 text-sm font-medium text-white",
        "transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70",
        className
      )}
    >
      {isLoading ? "Please wait..." : children}
    </button>
  );
}
