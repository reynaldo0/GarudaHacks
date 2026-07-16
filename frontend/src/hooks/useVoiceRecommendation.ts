"use client";

import { useEffect, useRef, useCallback } from "react";
import { Recommendation } from "@/types";

const COOLDOWN_MS = 20000;

const carNameId: Record<number, string> = {
  1: "satu", 2: "dua", 3: "tiga", 4: "empat", 5: "lima",
  6: "enam", 7: "tujuh", 8: "delapan", 9: "sembilan", 10: "sepuluh",
};

const carNameEn: Record<number, string> = {
  1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
  6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
};

function speakSequential(texts: { text: string; lang: "id" | "en" }[]) {
  if (typeof window === "undefined") return;
  const synth = window.speechSynthesis;
  synth.cancel();

  texts.forEach(({ text, lang }) => {
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang === "id" ? "id-ID" : "en-US";
    u.rate = 0.95;
    u.pitch = 1.0;
    u.volume = 1.0;

    const voices = synth.getVoices();
    const voice = voices.find((v) => v.lang.startsWith(lang));
    if (voice) u.voice = voice;

    synth.speak(u);
  });
}

function buildIdText(rec: Recommendation): string {
  const fromName = carNameId[rec.fromCarId] || String(rec.fromCarId);
  const toName = carNameId[rec.recommendations[0]?.toCarId] || String(rec.recommendations[0]?.toCarId);
  const women = rec.recommendations[0]?.isWomenPriority ? " khusus wanita" : "";
  return `Perhatian. Gerbong ${fromName} penuh. Kepada seluruh penumpang di gerbong ${fromName}, dimohon untuk berpindah ke gerbong ${toName}${women}. Terima kasih.`;
}

function buildEnText(rec: Recommendation): string {
  const fromName = carNameEn[rec.fromCarId] || String(rec.fromCarId);
  const toName = carNameEn[rec.recommendations[0]?.toCarId] || String(rec.recommendations[0]?.toCarId);
  const women = rec.recommendations[0]?.isWomenPriority ? ", women only" : "";
  return `Attention. Car ${fromName} is full. Passengers in car ${fromName}, please move to car ${toName}${women}. Thank you.`;
}

export function useVoiceRecommendation(recommendation: Recommendation | null) {
  const lastSpokenRef = useRef<string>("");
  const cooldownRef = useRef<NodeJS.Timeout | null>(null);

  const speak = useCallback((rec: Recommendation) => {
    const key = `${rec.fromCarId}-${rec.recommendations.map((r) => r.toCarId).join(",")}`;
    if (key === lastSpokenRef.current) return;

    if (cooldownRef.current) clearTimeout(cooldownRef.current);

    lastSpokenRef.current = key;
    cooldownRef.current = setTimeout(() => {
      lastSpokenRef.current = "";
    }, COOLDOWN_MS);

    speakSequential([
      { text: buildIdText(rec), lang: "id" },
      { text: buildEnText(rec), lang: "en" },
    ]);
  }, []);

  useEffect(() => {
    if (recommendation && recommendation.recommendations?.length > 0) {
      speak(recommendation);
    }
    return () => {
      if (cooldownRef.current) clearTimeout(cooldownRef.current);
    };
  }, [recommendation, speak]);
}
