import { create } from "zustand";

interface FitObjState {
	fitObj: string | null;
	setFitObj: (obj: string | null) => void;
}

const useFitObjStore = create<FitObjState>((set) => ({
	fitObj: null,
	setFitObj: (fitObj) => set({ fitObj }),
}));

export default useFitObjStore;
