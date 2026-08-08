import { AnimatePresence, motion } from "framer-motion";
import { LogOut, Settings, User, UserCircle2 } from "lucide-react";
import { useRef, useState } from "react";

import type { SectionId } from "@/api/ai";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const LINKS: { id: SectionId; label: string }[] = [
  { id: "home", label: "Home" },
  { id: "analysis", label: "Analysis" },
  { id: "studio", label: "Video Studio" },
  { id: "shorts", label: "Shorts Factory" },
];

export function NavBar({
  active,
  onNavigate,
}: {
  active: SectionId;
  onNavigate: (id: SectionId) => void;
}) {
  const [hovered, setHovered] = useState<SectionId | null>(null);
  const [loggedIn, setLoggedIn] = useState(false);
  const barRef = useRef<HTMLDivElement>(null);
  const [pointer, setPointer] = useState({ x: 0, y: 0, visible: false });

  const liquidOn = hovered ?? active;

  return (
    <nav className="fixed top-0 right-0 z-50 p-4 sm:p-6">
      <div
        ref={barRef}
        onMouseMove={(e) => {
          const rect = barRef.current?.getBoundingClientRect();
          if (!rect) return;
          setPointer({ x: e.clientX - rect.left, y: e.clientY - rect.top, visible: true });
        }}
        onMouseLeave={() => {
          setHovered(null);
          setPointer((p) => ({ ...p, visible: false }));
        }}
        className="glass-panel relative flex items-center gap-1 overflow-hidden rounded-full px-2 py-1.5"
      >
        {/* Liquid pointer follower — present on every interaction, not just the first */}
        <AnimatePresence>
          {pointer.visible && (
            <motion.span
              className="pointer-events-none absolute -z-0 h-16 w-16 rounded-full"
              style={{
                background:
                  "radial-gradient(circle, oklch(0.72 0.3 340 / 0.42) 0%, transparent 70%)",
                filter: "blur(6px)",
              }}
              initial={{ opacity: 0, scale: 0.6 }}
              animate={{ opacity: 1, scale: 1, left: pointer.x - 32, top: pointer.y - 32 }}
              exit={{ opacity: 0, scale: 0.6 }}
              transition={{ type: "spring", stiffness: 220, damping: 18, mass: 0.5 }}
            />
          )}
        </AnimatePresence>

        {LINKS.map((link) => (
          <button
            key={link.id}
            type="button"
            onMouseEnter={() => setHovered(link.id)}
            onClick={() => onNavigate(link.id)}
            className="relative z-10 rounded-full px-3 py-2 text-xs font-medium tracking-wide text-foreground/75 transition-colors hover:text-foreground sm:px-4 sm:text-sm"
          >
            {liquidOn === link.id && (
              <motion.span
                layoutId="gwen-nav-liquid"
                className="absolute inset-0 -z-10 rounded-full border border-primary/40 bg-primary/15"
                style={{ boxShadow: "0 0 22px oklch(0.72 0.3 340 / 0.35)" }}
                transition={{ type: "spring", stiffness: 260, damping: 24, mass: 0.6 }}
              />
            )}
            <span className={active === link.id ? "neon-text" : undefined}>{link.label}</span>
          </button>
        ))}

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              aria-label="Account"
              onMouseEnter={() => setHovered(null)}
              className="relative z-10 ml-1 rounded-full p-2 text-foreground/75 transition-colors hover:text-primary"
            >
              <UserCircle2 className="h-5 w-5" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            {loggedIn ? (
              <>
                <DropdownMenuLabel>Signed in</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" /> View profile
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" /> Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setLoggedIn(false)}>
                  <LogOut className="mr-2 h-4 w-4" /> Log out
                </DropdownMenuItem>
              </>
            ) : (
              <>
                <DropdownMenuLabel>Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {/* OAuth pending from backend — login trigger is mocked for now. */}
                <DropdownMenuItem onClick={() => setLoggedIn(true)}>Log in</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setLoggedIn(true)}>Sign up</DropdownMenuItem>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </nav>
  );
}
