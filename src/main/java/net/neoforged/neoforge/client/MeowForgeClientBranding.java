/*
 * Copyright (c) Forge Development LLC and contributors
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.neoforged.neoforge.client;

import com.mojang.blaze3d.platform.NativeImage;
import java.io.IOException;
import java.nio.ByteBuffer;
import net.minecraft.client.Minecraft;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.glfw.GLFWImage;
import org.lwjgl.system.MemoryStack;
import org.lwjgl.system.MemoryUtil;

@EventBusSubscriber(modid = "neoforge", value = Dist.CLIENT, bus = EventBusSubscriber.Bus.MOD)
public final class MeowForgeClientBranding {
    private MeowForgeClientBranding() {}

    @SubscribeEvent
    public static void clientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            try (var input = MeowForgeClientBranding.class.getResourceAsStream("/meowforge_icon.png")) {
                if (input == null) throw new IOException("Missing MeowForge icon");
                try (NativeImage image = NativeImage.read(input); MemoryStack stack = MemoryStack.stackPush()) {
                    ByteBuffer pixels = MemoryUtil.memAlloc(image.getWidth() * image.getHeight() * 4);
                    try {
                        pixels.asIntBuffer().put(image.getPixelsRGBA());
                        GLFWImage.Buffer icons = GLFWImage.malloc(1, stack);
                        icons.width(image.getWidth()).height(image.getHeight()).pixels(pixels);
                        GLFW.glfwSetWindowIcon(Minecraft.getInstance().getWindow().getWindow(), icons);
                    } finally {
                        MemoryUtil.memFree(pixels);
                    }
                }
            } catch (IOException error) {
                org.slf4j.LoggerFactory.getLogger(MeowForgeClientBranding.class).warn("Could not set MeowForge window icon", error);
            }
        });
    }
}
