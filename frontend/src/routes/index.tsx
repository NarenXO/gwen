import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { SectionId } from "@/api/ai";
import { AnalysisSection } from "@/components/gwen/AnalysisSection";
import { ChatAgent } from "@/components/gwen/ChatAgent";
import { HomeHero } from "@/components/gwen/HomeHero";
import { LandingSequence, landingAlreadyPlayed } from "@/components/gwen/LandingSequence";
import { NavBar } from "@/components/gwen/NavBar";
import { ShortsFactorySection } from "@/components/gwen/ShortsFactorySection";
import { VideoStudioSection } from "@/components/gwen/VideoStudioSection";
import { WebBackground } from "@/components/gwen/WebBackground";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "GWEN — AI YouTube Creator Manager" },
      {
        name: "description",
        content:
          "GWEN is an AI YouTube creator manager: channel intelligence, video and thumbnail diagnosis, and auto-generated shorts in one place.",
      },
      { property: "og:title", content: "GWEN — AI YouTube Creator Manager" },
      {
        property: "og:description",
        content:
          "Channel intelligence, content optimization and auto-generated shorts, managed by an AI agent.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: GwenPage,
});

function GwenPage() {
  const [landing, setLanding] = useState(false);
  const [active, setActive] = useState<SectionId>("home");

  const homeRef = useRef<HTMLElement>(null);
  const analysisRef = useRef<HTMLElement>(null);
  const studioRef = useRef<HTMLElement>(null);
  const shortsRef = useRef<HTMLElement>(null);

  const refs = useMemo(
    () => ({
      home: homeRef,
      analysis: analysisRef,
      studio: studioRef,
      shorts: shortsRef,
    }),
    [],
  );

  // Landing sequence plays once per browser session.
  useEffect(() => {
    if (!landingAlreadyPlayed()) setLanding(true);
  }, []);

  const navigate = useCallback(
    (id: SectionId) => {
      refs[id].current?.scrollIntoView({ behavior: "smooth" });
    },
    [refs],
  );

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        const id = visible?.target.getAttribute("data-section") as SectionId | undefined;
        if (id) setActive(id);
      },
      { threshold: [0.35, 0.6] },
    );
    Object.values(refs).forEach((r: React.RefObject<HTMLElement | null>) => {
      if (r.current) observer.observe(r.current);
    });
    return () => observer.disconnect();
  }, [refs]);

  return (
    <div className="relative">
      <WebBackground />
      {landing && <LandingSequence onDone={() => setLanding(false)} />}

      <NavBar active={active} onNavigate={navigate} />

      <main>
        <section ref={refs.home} data-section="home">
          <HomeHero hideLogo={landing} />
        </section>
        <section ref={refs.analysis} data-section="analysis">
          <AnalysisSection />
        </section>
        <section ref={refs.studio} data-section="studio">
          <VideoStudioSection />
        </section>
        <section ref={refs.shorts} data-section="shorts">
          <ShortsFactorySection />
        </section>
      </main>

      <ChatAgent section={active} />
    </div>
  );
}
