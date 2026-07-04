import { component$ } from "@qwik.dev/core";

export const Header = component$(() => {
    return (
        <header class="bg-white border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                        <span class="text-white font-bold text-sm">Q</span>
                    </div>
                    <span class="text-xl font-bold text-gray-900">Qwik</span>
                </div>
                <div class="flex items-center gap-4">
                    <a
                        href="#"
                        class="text-sm text-gray-600 hover:text-gray-900"
                    >
                        Sign In
                    </a>
                    <a
                        href="#"
                        class="text-sm bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors"
                    >
                        Get Started
                    </a>
                </div>
            </div>
        </header>
    );
});
