import clsx from "clsx";
import type { InputHTMLAttributes } from "react";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};

export default function Input({ label, error, className, ...props }: InputProps) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        {...props}
        className={clsx(
          "h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm",
          "focus:border-brand-500 focus:ring-2 focus:ring-brand-100",
          error && "border-red-400 focus:border-red-500 focus:ring-red-100",
          className
        )}
      />
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </label>
  );
}
