import { create } from "zustand";

interface GenerationState {
	isGenerating: boolean;
	setIsGenerating: (isGenerating: boolean) => void;
}

const useGenerationStore = create<GenerationState>((set) => ({
	isGenerating: false,
	setIsGenerating: (isGenerating) => set({ isGenerating }),
}));

export default useGenerationStore;
