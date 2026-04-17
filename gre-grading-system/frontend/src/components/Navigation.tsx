"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Home", icon: "🏠" },
  { href: "/practice", label: "Practice", icon: "✍️" },
  { href: "/history", label: "History", icon: "📚" },
  { href: "/progress", label: "Progress", icon: "📈" },
];

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📝</span>
            <span className="font-bold text-xl text-primary-700">
              GRE Essay Grader
            </span>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition",
                  pathname === item.href
                    ? "bg-primary-100 text-primary-700"
                    : "text-gray-600 hover:bg-gray-100",
                )}
              >
                <span className="mr-1">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>

          {/* Student ID (demo) */}
          <div className="text-sm text-gray-500">
            <span className="bg-gray-100 px-3 py-1 rounded-full">
              Demo Student
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
}
