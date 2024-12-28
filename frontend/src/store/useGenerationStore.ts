import { create } from "zustand";

interface GenerationState {
	isGenerating: boolean;
	generatingDone: boolean;
	setIsGenerating: (isGenerating: boolean) => void;
	setGeneratingDone: (generatingDone: boolean) => void;
}

const useGenerationStore = create<GenerationState>((set) => ({
	isGenerating: false,
	generatingDone: false,
	setIsGenerating: (isGenerating) => set({ isGenerating }),
	setGeneratingDone: (generatingDone) => set({ generatingDone }),
}));

export default useGenerationStore;
