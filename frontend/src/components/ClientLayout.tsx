"use client";

import { useSyncExternalStore } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";

export function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLandingPage = pathname === "/";

  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );

  if (!mounted) {
    return (
      <body className="min-h-full bg-background">
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      </body>
    );
  }

  if (isLandingPage) {
    return <body className="min-h-full bg-background">{children}</body>;
  }

  return (
    <body className="min-h-full flex bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 overflow-auto">{children}</main>
    </body>
  );
}
