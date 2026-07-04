import { component$ } from "@qwik.dev/core";

export const Footer = component$(() => {
    return (
        <footer class="bg-gray-900 text-gray-400 py-8">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                    <div class="flex items-center gap-2">
                        <div class="w-6 h-6 bg-primary rounded flex items-center justify-center">
                            <span class="text-white font-bold text-xs">Q</span>
                        </div>
                        <span class="text-sm font-semibold text-gray-300">
                            Qwik
                        </span>
                    </div>
                    <p class="text-sm">
                        &copy; 2026 Qwik Template. All rights reserved.
                    </p>
                    <div class="flex gap-6 text-sm">
                        <a href="#" class="hover:text-gray-200">
                            Terms
                        </a>
                        <a href="#" class="hover:text-gray-200">
                            Privacy
                        </a>
                        <a href="#" class="hover:text-gray-200">
                            Contact
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    );
});
