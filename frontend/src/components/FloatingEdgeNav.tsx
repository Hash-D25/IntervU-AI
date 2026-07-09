"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState, type ComponentType, type CSSProperties, type ReactNode } from "react";

import {
  IconAppMark,
  IconContact,
  IconDashboard,
  IconInterview,
  IconLogin,
  IconLogout,
  IconResume,
} from "@/components/icons";
import { useAuth } from "@/features/auth";

type IconComponent = ComponentType<{ className?: string }>;

type NavItem = {
  href: string;
  label: string;
  Icon: IconComponent;
  isActive: (pathname: string) => boolean;
};

const NAV_ITEMS: NavItem[] = [
  {
    href: "/",
    label: "Home",
    Icon: IconAppMark,
    isActive: (pathname) => pathname === "/",
  },
  {
    href: "/dashboard",
    label: "Dashboard",
    Icon: IconDashboard,
    isActive: (pathname) => pathname === "/dashboard",
  },
  {
    href: "/resumes",
    label: "Resumes",
    Icon: IconResume,
    isActive: (pathname) => pathname === "/resumes",
  },
  {
    href: "/interviews/new",
    label: "New interview",
    Icon: IconInterview,
    isActive: (pathname) => pathname.startsWith("/interviews"),
  },
  {
    href: "/contact",
    label: "Contact",
    Icon: IconContact,
    isActive: (pathname) => pathname === "/contact",
  },
];

type DockSlot = {
  key: string;
  label: string;
  node: ReactNode;
};

function getInitials(fullName: string, email: string): string {
  const trimmed = fullName.trim();
  if (trimmed && trimmed.toLowerCase() !== "string") {
    const parts = trimmed.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) {
      return `${parts[0]?.[0] ?? ""}${parts[1]?.[0] ?? ""}`.toUpperCase();
    }
    return trimmed.slice(0, 2).toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
}

function displayName(fullName: string, email: string): string {
  const trimmed = fullName.trim();
  if (trimmed && trimmed.toLowerCase() !== "string") {
    return trimmed;
  }
  return email;
}

function getDockTransform(index: number, hoveredIndex: number | null): CSSProperties {
  if (hoveredIndex === null) {
    return { transform: "translateX(0) scale(1)" };
  }

  const distance = Math.abs(index - hoveredIndex);

  if (distance === 0) {
    return { transform: "translateX(12px) scale(1.18)" };
  }

  const direction = index < hoveredIndex ? -1 : 1;

  if (distance === 1) {
    return { transform: `translateY(${direction * 11}px) scale(1.06)` };
  }

  if (distance === 2) {
    return { transform: `translateY(${direction * 6}px) scale(1.03)` };
  }

  return { transform: "translateX(0) scale(1)" };
}

type NavIconTileProps = {
  Icon: IconComponent;
  active?: boolean;
  mobile?: boolean;
  iconClassName?: string;
};

function NavIconTile({ Icon, active = false, mobile = false, iconClassName }: NavIconTileProps) {
  const tileClass = mobile ? "nav-icon-tile-mobile" : "nav-icon-tile";
  const stateClass = active ? "nav-icon-tile-active" : "nav-icon-tile-inactive";

  return (
    <span className={`${tileClass} ${stateClass}`}>
      <Icon
        className={`${mobile ? "h-6 w-6" : "h-7 w-7"} ${active ? "nav-icon-glow" : ""} ${iconClassName ?? ""}`}
      />
    </span>
  );
}

type NavDockItemProps = {
  index: number;
  label: string;
  hoveredIndex: number | null;
  onHover: (index: number) => void;
  children: ReactNode;
};

function NavDockItem({ index, label, hoveredIndex, onHover, children }: NavDockItemProps) {
  return (
    <div
      className="nav-dock-item"
      style={getDockTransform(index, hoveredIndex)}
      data-hovered={hoveredIndex === index ? "true" : "false"}
      onMouseEnter={() => onHover(index)}
    >
      {children}
      <span className="nav-hover-label" role="tooltip">
        {label}
      </span>
    </div>
  );
}

type DesktopNavDockProps = {
  slots: DockSlot[];
};

function DesktopNavDock({ slots }: DesktopNavDockProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <div className="nav-dock" onMouseLeave={() => setHoveredIndex(null)}>
      {slots.map((slot, index) => (
        <NavDockItem
          key={slot.key}
          index={index}
          label={slot.label}
          hoveredIndex={hoveredIndex}
          onHover={setHoveredIndex}
        >
          {slot.node}
        </NavDockItem>
      ))}
    </div>
  );
}

export function FloatingEdgeNav() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();

  const desktopSlots = useMemo<DockSlot[]>(() => {
    const slots: DockSlot[] = [];

    if (isAuthenticated && user) {
      slots.push({
        key: "profile",
        label: displayName(user.full_name, user.email),
        node: (
          <span
            className="nav-icon-tile nav-icon-tile-active text-sm font-semibold"
            title={user.full_name || user.email}
          >
            {getInitials(user.full_name, user.email)}
          </span>
        ),
      });
    } else {
      slots.push({
        key: "login",
        label: "Sign in",
        node: (
          <Link href="/login" aria-label="Sign in" className="flex justify-center">
            <NavIconTile Icon={IconLogin} />
          </Link>
        ),
      });
    }

    for (const item of NAV_ITEMS) {
      const active = item.isActive(pathname);
      slots.push({
        key: item.href,
        label: item.label,
        node: (
          <Link
            href={item.href}
            aria-label={item.label}
            aria-current={active ? "page" : undefined}
            className="flex justify-center"
          >
            <NavIconTile Icon={item.Icon} active={active} />
          </Link>
        ),
      });
    }

    if (isAuthenticated) {
      slots.push({
        key: "logout",
        label: "Sign out",
        node: (
          <button
            type="button"
            onClick={() => void logout()}
            aria-label="Sign out"
            className="flex justify-center"
          >
            <span className="nav-icon-tile nav-icon-tile-inactive text-rose-400/80 hover:border-rose-400/25 hover:text-rose-300">
              <IconLogout className="h-7 w-7" />
            </span>
          </button>
        ),
      });
    }

    return slots;
  }, [isAuthenticated, logout, pathname, user]);

  return (
    <>
      {/* Desktop - mac-style floating dock */}
      <aside
        className="fixed left-4 top-1/2 z-50 hidden -translate-y-1/2 overflow-visible sm:block"
        aria-label="Main navigation"
      >
        <DesktopNavDock slots={desktopSlots} />
      </aside>

      {/* Mobile - floating bottom bar */}
      <nav
        className="fixed bottom-4 left-1/2 z-50 flex max-w-[calc(100vw-2rem)] -translate-x-1/2 items-center gap-2 overflow-x-auto px-1 py-1 sm:hidden"
        aria-label="Main navigation"
      >
        {NAV_ITEMS.map((item) => {
          const active = item.isActive(pathname);
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-label={item.label}
              aria-current={active ? "page" : undefined}
              className="shrink-0"
            >
              <NavIconTile Icon={item.Icon} active={active} mobile />
            </Link>
          );
        })}
        {isAuthenticated ? (
          <button
            type="button"
            onClick={() => void logout()}
            aria-label="Sign out"
            className="shrink-0"
          >
            <span className="nav-icon-tile-mobile nav-icon-tile-inactive text-rose-400/80">
              <IconLogout className="h-6 w-6" />
            </span>
          </button>
        ) : (
          <Link href="/login" aria-label="Sign in" className="shrink-0">
            <NavIconTile Icon={IconLogin} mobile />
          </Link>
        )}
      </nav>
    </>
  );
}
