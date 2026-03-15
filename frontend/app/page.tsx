"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { getStoredToken } from "@/lib/auth";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace(getStoredToken() ? "/dashboard" : "/login");
  }, [router]);

  return <main className="centered-shell">Chargement...</main>;
}
