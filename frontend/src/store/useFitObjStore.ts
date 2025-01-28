import { create } from "zustand";

interface FitObjState {
	fitObj: string | null;
	setFitObj: (obj: string | null) => void;
	isFitObjLoading: boolean;
	setIsFitObjLoading: (isLoading: boolean) => void;
}

const useFitObjStore = create<FitObjState>((set) => ({
	fitObj: null,
	setFitObj: (fitObj) => set({ fitObj }),
	isFitObjLoading: false,
	setIsFitObjLoading: (isFitObjLoading) => set({ isFitObjLoading }),
}));

export default useFitObjStore;
