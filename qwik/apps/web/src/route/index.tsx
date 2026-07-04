import { component$ } from "@qwik.dev/core";
import "../style/global.css";

export default component$(() => {
    return (
        <div class="bg-white">
            <section class="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
                    <div class="max-w-3xl mx-auto text-center">
                        <h1 class="text-4xl md:text-6xl font-bold tracking-tight mb-6">
                            Welcome to <span class="text-primary">Qwik</span>
                        </h1>
                        <p class="text-lg md:text-xl text-gray-300 mb-8">
                            The fastest way to build modern web applications.
                            Start with this template and build something
                            amazing.
                        </p>
                        <div class="flex flex-wrap justify-center gap-4">
                            <a
                                href="#"
                                class="inline-flex items-center px-6 py-3 bg-primary text-white font-semibold rounded-lg hover:bg-primary-dark transition-colors"
                            >
                                Get Started
                            </a>
                            <a
                                href="#"
                                class="inline-flex items-center px-6 py-3 border border-gray-500 text-gray-300 font-semibold rounded-lg hover:bg-gray-800 transition-colors"
                            >
                                Learn More
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            <section class="py-16 md:py-24 bg-gray-50">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                        Built with Qwik
                    </h2>
                    <p class="text-lg text-gray-600 max-w-2xl mx-auto">
                        This is a Qwik project template. Edit{" "}
                        <code class="bg-gray-200 px-2 py-1 rounded text-sm">
                            src/route/index.tsx
                        </code>{" "}
                        to get started.
                    </p>
                </div>
            </section>
        </div>
    );
});
