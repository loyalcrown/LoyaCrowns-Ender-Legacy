package com.loyacrown.enderlegacy.util;

import com.loyacrown.enderlegacy.blockentity.DimensionalTransceiverBlockEntity;
import com.loyacrown.enderlegacy.blockentity.DimensionalTransceiverBlockEntity.ResourceType;
import net.minecraft.server.MinecraftServer;

import java.util.Collections;
import java.util.Map;
import java.util.Set;
import java.util.List;
import java.util.ArrayList;
import java.util.TreeSet;
import java.util.WeakHashMap;
import java.util.function.Predicate;

/**
 * Server-local runtime index for legacy Dimensional Transceivers.
 *
 * The 1.12.2 machine had independent POWER, ITEM and FLUID channel lists and
 * both public and player-owned private channels. Keeping a single weak node set
 * lets the modern port match those properties without duplicating machines in
 * several indexes when their settings change.
 */
public final class DimensionalTransceiverNetwork {
    private static final Map<MinecraftServer, Set<DimensionalTransceiverBlockEntity>> NETWORKS = new WeakHashMap<>();

    public static synchronized void register(DimensionalTransceiverBlockEntity blockEntity) {
        MinecraftServer server = blockEntity.getServer();
        if (server == null) return;
        NETWORKS.computeIfAbsent(server, ignored -> Collections.newSetFromMap(new WeakHashMap<>()))
                .add(blockEntity);
    }

    public static synchronized void unregister(DimensionalTransceiverBlockEntity blockEntity) {
        MinecraftServer server = blockEntity.getServer();
        if (server == null) return;
        Set<DimensionalTransceiverBlockEntity> nodes = NETWORKS.get(server);
        if (nodes != null) nodes.remove(blockEntity);
    }

    public static synchronized DimensionalTransceiverBlockEntity findPeer(
            DimensionalTransceiverBlockEntity source,
            ResourceType resourceType,
            Predicate<DimensionalTransceiverBlockEntity> predicate) {
        MinecraftServer server = source.getServer();
        if (server == null) return null;
        Set<DimensionalTransceiverBlockEntity> nodes = NETWORKS.get(server);
        if (nodes == null) return null;
        nodes.removeIf(be -> be == null || be.isRemoved());
        for (DimensionalTransceiverBlockEntity candidate : nodes) {
            if (candidate == source) continue;
            if (!source.canConnectTo(candidate, resourceType)) continue;
            if (predicate.test(candidate)) return candidate;
        }
        return null;
    }

    /**
     * Returns the currently discoverable legacy channels for the selected resource type.
     * Public channels are visible to everyone. Private channels are scoped to the owner,
     * mirroring the old public/private channel lists without leaking another player's names.
     */
    public static synchronized List<String> listChannels(
            DimensionalTransceiverBlockEntity source,
            ResourceType resourceType,
            boolean privateOnly) {
        TreeSet<String> names = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
        names.add("default");
        names.add(source.getChannel(resourceType));
        MinecraftServer server = source.getServer();
        if (server == null) return new ArrayList<>(names);
        Set<DimensionalTransceiverBlockEntity> nodes = NETWORKS.get(server);
        if (nodes == null) return new ArrayList<>(names);
        nodes.removeIf(be -> be == null || be.isRemoved());
        for (DimensionalTransceiverBlockEntity candidate : nodes) {
            if (candidate.isPrivate(resourceType) != privateOnly) continue;
            if (privateOnly) {
                if (source.getOwner() == null || !source.getOwner().equals(candidate.getOwner())) continue;
            }
            String name = candidate.getChannel(resourceType);
            if (name != null && !name.isBlank()) names.add(name);
        }
        return new ArrayList<>(names);
    }

    /** Compatibility overload used by the restored Ender Rail. */
    public static synchronized DimensionalTransceiverBlockEntity findPeer(
            DimensionalTransceiverBlockEntity source,
            Predicate<DimensionalTransceiverBlockEntity> predicate) {
        return findPeer(source, ResourceType.POWER, predicate);
    }

    private DimensionalTransceiverNetwork() {}
}
