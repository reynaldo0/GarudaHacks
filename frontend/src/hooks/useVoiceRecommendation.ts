"use client";

import { useEffect, useRef, useCallback } from "react";
import { Recommendation } from "@/types";

const COOLDOWN_MS = 15000;

const carName: Record<number, string> = {
  1: "satu", 2: "dua", 3: "tiga", 4: "empat", 5: "lima",
  6: "enam", 7: "tujuh", 8: "delapan", 9: "sembilan", 10: "sepuluh",
};

function speakIndonesian(text: string) {
  if (typeof window === "undefined") return;
  const synth = window.speechSynthesis;
  synth.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "id-ID";
  u.rate = 0.95;
  u.pitch = 1.0;
  u.volume = 1.0;

  const voices = synth.getVoices();
  const idVoice = voices.find((v) => v.lang.startsWith("id"));
  if (idVoice) u.voice = idVoice;

  synth.speak(u);
}

export function useVoiceRecommendation(recommendation: Recommendation | null) {
  const lastSpokenRef = useRef<string>("");
  const cooldownRef = useRef<NodeJS.Timeout | null>(null);

  const speak = useCallback((rec: Recommendation) => {
    const key = `${rec.fromCarId}-${rec.toCarId}`;
    if (key === lastSpokenRef.current) return;

    if (cooldownRef.current) clearTimeout(cooldownRef.current);

    lastSpokenRef.current = key;
    cooldownRef.current = setTimeout(() => {
      lastSpokenRef.current = "";
    }, COOLDOWN_MS);

    const fromName = carName[rec.fromCarId] || String(rec.fromCarId);
    const toName = carName[rec.toCarId] || String(rec.toCarId);

    const fromPct = Math.round(rec.confidence * 100);
    const text =
      `Perhatian. Gerbong ${fromName} penuh. ` +
      `Disarankan memindahkan penumpang dari gerbong ${fromName} ke gerbong ${toName} yang terdekat. ` +
      `Tingkat kepercayaan ${fromPct} persen.`;

    speakIndonesian(text);
  }, []);

  useEffect(() => {
    if (recommendation) {
      speak(recommendation);
    }
    return () => {
      if (cooldownRef.current) clearTimeout(cooldownRef.current);
    };
  }, [recommendation, speak]);
}
