import { create } from "zustand";

interface ImageState {
	image: string | null;
	setImage: (image: string | null) => void;
}

const useImageStore = create<ImageState>((set) => ({
	image: null,
	setImage: (image) => set({ image }),
}));

export default useImageStore;
