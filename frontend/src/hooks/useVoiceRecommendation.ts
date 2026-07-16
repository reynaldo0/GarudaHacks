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
  const toName = carNameId[rec.toCarId] || String(rec.toCarId);
  const pct = Math.round(rec.confidence * 100);
  const isWomen = rec.isWomenPriority;
  const lines: string[] = [];

  lines.push(`Perhatian. Gerbong ${fromName} ${isWomen ? "khusus wanita" : ""} penuh.`);
  lines.push(`Disarankan memindahkan penumpang dari gerbong ${fromName} ke gerbong ${toName} ${isWomen ? "khusus wanita" : ""}.`);
  lines.push(`Tingkat kepercayaan ${pct} persen.`);

  if (rec.womenAlternative) {
    const wFrom = carNameId[rec.womenAlternative.fromCarId] || String(rec.womenAlternative.fromCarId);
    const wTo = carNameId[rec.womenAlternative.toCarId] || String(rec.womenAlternative.toCarId);
    lines.push(`Alternatif untuk penumpang wanita. Pindahkan dari gerbong ${wFrom} ke gerbong ${wTo} khusus wanita.`);
  }

  return lines.join(" ");
}

function buildEnText(rec: Recommendation): string {
  const fromName = carNameEn[rec.fromCarId] || String(rec.fromCarId);
  const toName = carNameEn[rec.toCarId] || String(rec.toCarId);
  const pct = Math.round(rec.confidence * 100);
  const isWomen = rec.isWomenPriority;
  const lines: string[] = [];

  lines.push(`Attention. Car ${fromName} ${isWomen ? "women only" : ""} is full.`);
  lines.push(`Please move passengers from car ${fromName} to car ${toName} ${isWomen ? "women only" : ""}.`);
  lines.push(`Confidence level ${pct} percent.`);

  if (rec.womenAlternative) {
    const wFrom = carNameEn[rec.womenAlternative.fromCarId] || String(rec.womenAlternative.fromCarId);
    const wTo = carNameEn[rec.womenAlternative.toCarId] || String(rec.womenAlternative.toCarId);
    lines.push(`Alternative for women passengers. Move from car ${wFrom} to women only car ${wTo}.`);
  }

  return lines.join(" ");
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

    const idText = buildIdText(rec);
    const enText = buildEnText(rec);

    speakSequential([
      { text: idText, lang: "id" },
      { text: enText, lang: "en" },
    ]);
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
