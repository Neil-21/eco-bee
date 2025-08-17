"use client";
import React from "react";
import IntakeForm from "./components/IntakeForm";

export default function Home() {
  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Eco-Bee Climate Snapshot</h1>
      <IntakeForm />
    </main>
  );
}
