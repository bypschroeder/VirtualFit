import { create } from "zustand";

interface ErrorState {
	generationError: string | null;
	setGenerationError: (generationError: string | null) => void;
	previewError: string | null;
	setPreviewError: (previewError: string | null) => void;
	tryOnError: string | null;
	setTryOnError: (tryOnError: string | null) => void;
}

const useErrorStore = create<ErrorState>((set) => ({
	generationError: null,
	setGenerationError: (generationError) => set({ generationError }),
	previewError: null,
	setPreviewError: (previewError) => set({ previewError }),
	tryOnError: null,
	setTryOnError: (tryOnError) => set({ tryOnError }),
}));

export default useErrorStore;
