"use client";

import { useState } from 'react';
import Link from 'next/link';

const navLinks = [
  { label: 'Home', href: '/' },
  { label: 'Features', href: '/#features' },
  { label: 'About', href: '/#about' },
  { label: 'Contact', href: '/#contact' },
];

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 sm:px-8 lg:px-10">
        <div>
          <Link href="/" className="text-lg font-semibold tracking-tight text-white sm:text-xl">
            HealthSense <span className="text-cyan-300">AI</span>
          </Link>
        </div>

        <nav className="hidden items-center gap-8 md:flex" aria-label="Primary navigation">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="text-sm font-medium text-slate-200 transition hover:text-white"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-4 md:flex">
          <Link
            href="/assessment"
            className="rounded-full bg-cyan-500 px-5 py-2.5 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:bg-cyan-400"
          >
            Start Assessment
          </Link>
        </div>

        <button
          type="button"
          aria-label="Toggle navigation menu"
          aria-expanded={isOpen}
          aria-controls="mobile-menu"
          className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-slate-950/80 text-slate-100 transition hover:border-slate-200/20 hover:bg-slate-900/80 md:hidden"
          onClick={() => setIsOpen((current) => !current)}
        >
          <span className="sr-only">Open main menu</span>
          <div className="flex h-5 w-5 flex-col justify-between">
            <span className={`block h-[2px] w-5 rounded-full bg-current transition ${isOpen ? 'translate-y-1.5 rotate-45' : ''}`} />
            <span className={`block h-[2px] w-5 rounded-full bg-current transition ${isOpen ? 'opacity-0' : ''}`} />
            <span className={`block h-[2px] w-5 rounded-full bg-current transition ${isOpen ? '-translate-y-1.5 -rotate-45' : ''}`} />
          </div>
        </button>
      </div>

      <div
        id="mobile-menu"
        className={`md:hidden border-t border-white/10 bg-slate-950/95 backdrop-blur-xl transition ${isOpen ? 'block' : 'hidden'}`}
      >
        <div className="space-y-4 px-6 py-5">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="block rounded-2xl px-4 py-3 text-base font-medium text-slate-100 transition hover:bg-slate-900/80"
              onClick={() => setIsOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <Link
            href="/assessment"
            className="block rounded-2xl bg-cyan-500 px-4 py-3 text-center text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
            onClick={() => setIsOpen(false)}
          >
            Start Assessment
          </Link>
        </div>
      </div>
    </header>
  );
}

