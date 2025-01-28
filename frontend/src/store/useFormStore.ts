import { create } from "zustand";

interface FormState {
	gender: "male" | "female" | undefined;
	height: number;
	setGender: (gender: "male" | "female" | undefined) => void;
	setHeight: (height: number) => void;
}

const useFormStore = create<FormState>((set) => ({
	gender: undefined,
	height: 0,
	setGender: (gender) => set({ gender }),
	setHeight: (height) => set({ height }),
}));

export default useFormStore;
