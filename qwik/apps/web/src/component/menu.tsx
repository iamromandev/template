import { component$ } from "@qwik.dev/core";

export const Menu = component$(() => {
    const links = [
        { label: "Home", href: "#", active: true },
        { label: "Docs", href: "#" },
        { label: "Components", href: "#" },
        { label: "Blog", href: "#" },
        { label: "Contact", href: "#" },
    ];

    return (
        <nav class="bg-gray-50 border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex gap-6 -mb-px">
                    {links.map((link) => (
                        <a
                            key={link.label}
                            href={link.href}
                            class={
                                "text-sm font-medium py-3 border-b-2 transition-colors " +
                                (link.active
                                    ? "border-primary text-primary"
                                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300")
                            }
                        >
                            {link.label}
                        </a>
                    ))}
                </div>
            </div>
        </nav>
    );
});
